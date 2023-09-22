from operategpt.prompt.lang import Language


class OperatePrompt:
    operate_prompt: str
    image_desc_prompt: str
    video_desc_prompt: str

    def __init__(
        self, operate_prompt: str, image_decs_prompt: str, video_desc_prompt: str
    ):
        self.operate_prompt = operate_prompt
        self.image_desc_prompt = image_decs_prompt
        self.video_desc_prompt = video_desc_prompt


class OperatePromptManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.prompts = {}
            print("INIT operate manager running!")
            prompt_en: OperatePrompt = OperatePrompt(
                OPERATE_PROMPT, IMAGE_DESC_PROMPT, VIDEO_DESC_PROMPT
            )
            prompt_zh: OperatePrompt = OperatePrompt(
                OPERATE_PROMPT_ZH, IMAGE_DESC_PROMPT_ZH, VIDEO_DESC_PROMPT_ZH
            )
            cls._instance.prompts[Language.ENGLISH.value] = prompt_en
            cls._instance.prompts[Language.CHINESE.value] = prompt_zh
            print("INIT operate manager succeed!")
        return cls._instance

    def add_prompt(self, scene_name: str, prompt: OperatePrompt):
        self.prompts[scene_name] = prompt

    def get_prompt(self, scene_name: str) -> OperatePrompt:
        return self.prompts.get(scene_name)

    @classmethod
    def get_instance(cls):
        return cls()


OPERATE_PROMPT = """Please write a article as long as possible according to the following content, the format is beautiful and the content is attractive. Remarks: Be sure to author and analyze according to the content provided, the author is OperateGPT, and may include charts as appropriate, generate in Markdown format, the author operateGPT should be linked to 'https://github.com/xuyuan23/operateGPT'.
content: 
```
{0}
```

To make the operational document appear more organized, please insert the following images at the different appropriate locations in the document, not the same locations, you can use the format such as `<img src='http://xxxxxxx.png'/>`, if the image list is empty, please ignore.
```
{1}
```

Please insert the following videos at the different appropriate locations in the document, not the same locations, you can use the format such as `<video width="640" height="360" controls> <source src="http://xxxxxx.mp4" type="video/mp4">video-name</video>`, if the video list is empty, please ignore.
```
{2}
```
"""

IMAGE_DESC_PROMPT = """Based on the content below, select 3 to 5 different relevant events or content information and describe them along with their respective characteristics with length of fewer than 100 words.:
```
{0}
```

Please provide an answer similar to the one below, but without any additional information, details start with <ImagePrompt>, end with </ImagePrompt>, no content beyound tag <ImagePrompt> and </ImagePrompt>. 
You should response me follow next format, only one json data with some key-value data:

<ImagePrompt> {{"picture-name-1": "<summary content1>", "picture-name-2": "<summary content2>", "picture-name-3": "<summary content3>"}} </ImagePrompt>

"""

VIDEO_DESC_PROMPT = """Based on the content below, summarize a core thing, as well as related functions and processes
```
{0}
```

Please provide an answer similar to the one below, but without any additional information, details start with <VideoPrompt>, end with </VideoPrompt>, no content beyound tag <VideoPrompt> and </VideoPrompt>. 
You should response me follow next format, only one json data with some key-value data:

<VideoPrompt> {{"video-name-1": "<summary content1>"}} </VideoPrompt>

"""


OPERATE_PROMPT_ZH = """请撰写一篇尽量长且详细的文章，根据以下内容编写。要求文章格式美观，内容吸引人。备注：请确保根据提供的内容进行撰写和分析，作者为OperateGPT。以Markdown格式生成，作者operateGPT请链接到'https://github.com/xuyuan23/operateGPT'
内容：
```
{0}
```

为了使文章结构更加美观，请将以下图片插入到文档的不同适当位置，不能是相同的位置，您可以使用 <img src='http://xxxxxxx.png'/> 这样的格式。如果图片列表为空，请忽略。
```
{1}
```

请将以下视频插入到文档的不同适当位置，不能是相同的位置，您可以使用 <video width="640" height="360" controls> <source src="http://xxxxxx.mp4" type="video/mp4">video-name</video> 这样的格式。如果视频列表为空，请忽略。
```
{2}
```

全文每张图片和视频只允许展示一次，也不允许在文章末尾单独罗列展示

"""

IMAGE_DESC_PROMPT_ZH = """根据以下内容，提取并总结出最少3个，最多5个相关的特征或者事件，并描述它们及其各自的特点，每个描述不超过50个字,要求返回内容全部是英文:
```
{0}
```

请提供一个类似下面的答案，详细信息从"<ImagePrompt>"开始，以"</ImagePrompt>"结束，标签"<ImagePrompt>"和"</ImagePrompt>"之外不包含任何内容，不允许提供无关的额外信息，您应该按照以下格式回复我，只有一个包含一些键值数据的 JSON 数据：

<ImagePrompt> {{"picture-name-1": "<summary content1>", "picture-name-2": "<summary content2>", "picture-name-3": "<summary content3>"}} </ImagePrompt>

"""

VIDEO_DESC_PROMPT_ZH = """根据以下内容，总结1个内容相关的行为、动作或者事件，并描述该事件或者行为的具体过程，描述不超过100个字,要求返回内容全部是英文。
```
{0}
```

请提供一个类似下面的答案，但不包含任何额外的信息，详细信息从"<VideoPrompt>"开始，以"</VideoPrompt>"结束，标签"<VideoPrompt>"和"</VideoPrompt>"之间不包含任何内容。您应该按照以下格式回复我，只有一个包含一些键值数据的 JSON 数据：

<VideoPrompt> {{"video-name-1": "<summary content1>"}} </VideoPrompt>

"""
